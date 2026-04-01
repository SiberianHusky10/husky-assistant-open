package tech.aihusky.huskyaiassistantuser.entry;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class User {
    private Long userId;
    private String email;
    private String password;
    private LocalDateTime createdAt;
    private LocalDateTime lastLoginTime;
    private String lastLoginIp;
    private String device;
    private String area;
    private Integer status;
}
