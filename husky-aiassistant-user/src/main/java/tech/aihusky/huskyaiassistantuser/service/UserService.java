package tech.aihusky.huskyaiassistantuser.service;

import org.mindrot.jbcrypt.BCrypt;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import tech.aihusky.huskyaiassistantuser.dto.RegisterRequest;
import tech.aihusky.huskyaiassistantuser.entry.User;
import tech.aihusky.huskyaiassistantuser.mapper.UserMapper;

@Service
public class UserService {

    @Autowired
    private UserMapper userMapper;

    public void register(RegisterRequest request) {

        // 1. 参数校验
        if (request.getEmail() == null || !request.getEmail().contains("@")) {
            throw new RuntimeException("邮箱格式不正确");
        }

        if (request.getPassword() == null || request.getPassword().length() < 6) {
            throw new RuntimeException("密码至少6位");
        }

        // 2. 检查是否已存在
        User exist = userMapper.findByEmail(request.getEmail());
        if (exist != null) {
            throw new RuntimeException("邮箱已存在");
        }

        // 3. 密码加密
        String encryptedPassword = BCrypt.hashpw(request.getPassword(), BCrypt.gensalt());

        // 4. 插入数据库
        User user = new User();
        user.setEmail(request.getEmail());
        user.setPassword(encryptedPassword);

        userMapper.insert(user);
    }
}
