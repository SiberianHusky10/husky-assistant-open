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

    @PostMapping("/register")
    public Map<String, Object> register(@RequestBody RegisterRequest request) {
        Map<String, Object> result = new HashMap<>();

        try {
            userService.register(request);
            result.put("code", 0);
            result.put("message", "注册成功");
        } catch (Exception e) {
            result.put("code", 1);
            result.put("message", e.getMessage());
        }

        return result;
    }
}
