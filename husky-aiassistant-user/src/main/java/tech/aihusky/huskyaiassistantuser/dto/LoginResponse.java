package tech.aihusky.huskyaiassistantuser.dto;
import lombok.Data;

@Data
public class LoginResponse {
    private Integer code = 0;
    private String message = "登录成功";
    private String token;           // JWT
    private Long userId;
    private String email;
    // 可加 user 其他信息
}
