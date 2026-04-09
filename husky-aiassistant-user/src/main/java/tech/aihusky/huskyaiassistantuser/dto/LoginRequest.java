package tech.aihusky.huskyaiassistantuser.dto;
import lombok.Data;

@Data
public class LoginRequest {
    private String email;
    private String password;
    // 可选：前端可传 device（浏览器指纹、User-Agent 解析等）
    private String device;
}
