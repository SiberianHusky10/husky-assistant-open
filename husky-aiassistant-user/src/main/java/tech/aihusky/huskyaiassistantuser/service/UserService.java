package tech.aihusky.huskyaiassistantuser.service;

import org.mindrot.jbcrypt.BCrypt;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import tech.aihusky.huskyaiassistantuser.dto.RegisterRequest;
import tech.aihusky.huskyaiassistantuser.entry.User;
import tech.aihusky.huskyaiassistantuser.mapper.UserMapper;

import java.security.SecureRandom;
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
}
