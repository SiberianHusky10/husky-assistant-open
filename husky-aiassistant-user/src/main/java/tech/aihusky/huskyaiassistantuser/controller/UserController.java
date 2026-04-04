package tech.aihusky.huskyaiassistantuser.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import tech.aihusky.huskyaiassistantuser.dto.RegisterRequest;
import tech.aihusky.huskyaiassistantuser.service.UserService;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class UserController {

    @Autowired
    private UserService userService;

    @PostMapping("/send-register-code")
    public Map<String, Object> sendRegisterCode(@RequestBody Map<String, String> req) {
        Map<String, Object> result = new HashMap<>();
        try {
            String email = req.get("email");
            userService.sendRegisterCode(email);
            result.put("code", 0);
            result.put("message", "验证码已发送至邮箱，请查收");
        } catch (Exception e) {
            result.put("code", 1);
            result.put("message", e.getMessage());
        }
        return result;
    }

    @PostMapping("/register")
    public Map<String, Object> register(@RequestBody RegisterRequest request) {
        Map<String, Object> result = new HashMap<>();
        try {
            // 注意：RegisterRequest 需要新增一个字段 String code
            userService.completeRegister(request, request.getCode());
            result.put("code", 0);
            result.put("message", "注册成功");
        } catch (Exception e) {
            result.put("code", 1);
            result.put("message", e.getMessage());
        }
        return result;
    }
}
