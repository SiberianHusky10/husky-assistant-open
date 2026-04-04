package tech.aihusky.huskyaiassistantuser.dto;

import lombok.Data;

@Data
public class RegisterRequest {
    private String email;
    private String password;
    private String code;
}
