package tech.aihusky.huskyaiassistantuser.service;

import org.apache.commons.lang3.StringUtils;
import org.mindrot.jbcrypt.BCrypt;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import tech.aihusky.huskyaiassistantuser.dto.LoginRequest;
import tech.aihusky.huskyaiassistantuser.dto.LoginResponse;
import tech.aihusky.huskyaiassistantuser.dto.RegisterRequest;
import tech.aihusky.huskyaiassistantuser.entry.User;
import tech.aihusky.huskyaiassistantuser.mapper.UserMapper;

import javax.servlet.http.HttpServletRequest;
import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Random;
import java.util.concurrent.TimeUnit;

@Service
public class UserService {

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private EmailService emailService;

    @Autowired
    private StringRedisTemplate redisTemplate;   // Redis 操作

    @Autowired
    private JwtService jwtService;   // 后面会创建

    private static final String VERIFY_CODE_PREFIX = "register:verify:";  // Redis key 前缀
    private static final long CODE_EXPIRE_MINUTES = 30;                   // 验证码有效期

    /**
     * 第一步：发送注册验证码
     */
    public void sendRegisterCode(String email) {
        // 1. 参数校验
        if (email == null || !email.contains("@")) {
            throw new RuntimeException("邮箱格式不正确");
        }

        // 2. 检查邮箱是否已注册
        User exist = userMapper.findByEmail(email);
        if (exist != null) {
            throw new RuntimeException("该邮箱已注册");
        }

        // 3. 生成6位验证码（推荐使用 SecureRandom，更安全）
        String code = generateSecureCode();

        // 4. 存入 Redis（带过期时间）
        String redisKey = VERIFY_CODE_PREFIX + email;
        redisTemplate.opsForValue().set(redisKey, code, CODE_EXPIRE_MINUTES, TimeUnit.MINUTES);

        // 5. 发送邮件（建议加上 @Async 异步）
        emailService.sendVerificationCode(email, code);
    }

    /**
     * 第二步：验证验证码并完成注册
     */
    public void completeRegister(RegisterRequest request, String inputCode) {
        // 1. 参数校验
        if (request.getEmail() == null || request.getPassword() == null || request.getPassword().length() < 6) {
            throw new RuntimeException("参数不正确");
        }

        // 2. 校验验证码
        String redisKey = VERIFY_CODE_PREFIX + request.getEmail();
        String savedCode = redisTemplate.opsForValue().get(redisKey);

        if (savedCode == null) {
            throw new RuntimeException("验证码已过期，请重新获取");
        }
        if (!savedCode.equals(inputCode)) {
            throw new RuntimeException("验证码错误");
        }

        // 3. 检查邮箱是否已注册（防止并发）
        User exist = userMapper.findByEmail(request.getEmail());
        if (exist != null) {
            throw new RuntimeException("该邮箱已注册");
        }

        // 4. 密码加密
        String encryptedPassword = BCrypt.hashpw(request.getPassword(), BCrypt.gensalt());

        // 5. 插入用户（复用你原来的逻辑）
        User user = new User();
        user.setEmail(request.getEmail());
        user.setPassword(encryptedPassword);
        // 如果你的 User 实体有其他字段（如 username），在这里设置
        // user.setStatus(1);  // 如果需要

        userMapper.insert(user);

        // 6. 删除已使用的验证码（防止重复使用）
        redisTemplate.delete(redisKey);
    }

    /**
     * 生成安全的6位数字验证码
     */
    private String generateSecureCode() {
        try {
            SecureRandom secureRandom = SecureRandom.getInstanceStrong();
            int number = secureRandom.nextInt(900000) + 100000;  // 100000 ~ 999999
            return String.valueOf(number);
        } catch (Exception e) {
            // 降级使用普通随机
            return String.format("%06d", new Random().nextInt(1000000));
        }
    }

    /**
     * 登录核心逻辑
     */
    public LoginResponse login(LoginRequest request, HttpServletRequest httpRequest) {
        // 1. 参数校验
        if (request.getEmail() == null || request.getPassword() == null) {
            throw new RuntimeException("邮箱或密码不能为空");
        }

        // 2. 查询用户
        User user = userMapper.findByEmail(request.getEmail());
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        if (user.getStatus() != null && user.getStatus() == 0) {
            throw new RuntimeException("账号已被禁用");
        }

        // 3. 密码校验（BCrypt）
        if (!BCrypt.checkpw(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("密码错误");
        }

        // 4. 更新最后登录信息（重要！）
        String ip = getClientIp(httpRequest);
        String area = getAreaByIp(ip);        // 可选：调用 IP 归属地接口或本地库
        String device = StringUtils.isNotBlank(request.getDevice()) ? request.getDevice() : parseUserAgent(httpRequest);

        user.setLastLoginTime(LocalDateTime.now());
        user.setLastLoginIp(ip);
        user.setArea(area);
        user.setDevice(device);

        userMapper.updateLoginInfo(user);     // 需要在 Mapper 加这个更新方法

        // 5. 生成 JWT
        String token = jwtService.generateToken(user.getUserId(), user.getEmail());

        // 6. 构造响应
        LoginResponse resp = new LoginResponse();
        resp.setToken(token);
        resp.setUserId(user.getUserId());
        resp.setEmail(user.getEmail());
        return resp;
    }

    // 获取客户端真实 IP（考虑 Nginx 等代理）
    private String getClientIp(HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("X-Real-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }
        // 可能有多个 IP，取第一个
        if (ip != null && ip.contains(",")) {
            ip = ip.split(",")[0].trim();
        }
        return ip;
    }

    // 简单 User-Agent 解析设备（可引入 ua-parser 库更准确）
    private String parseUserAgent(HttpServletRequest request) {
        String ua = request.getHeader("User-Agent");
        if (ua == null) return "Unknown";
        if (ua.contains("Mobile") || ua.contains("Android") || ua.contains("iPhone")) {
            return "Mobile";
        }
        return "Desktop";
    }

    // 可选：IP 归属地（可调用第三方 API 或用 ip2region 本地库）
    private String getAreaByIp(String ip) {
        // 暂时返回空，或实现 ip2region
        return "";
    }
}
