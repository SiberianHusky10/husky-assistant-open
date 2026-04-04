package tech.aihusky.huskyaiassistantuser.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Service
public class EmailService {

    @Autowired
    private JavaMailSender mailSender;

    // 从配置文件读取（避免写死）
    @Value("${spring.mail.username}")
    private String fromEmail;

    /**
     * 发送纯文本验证码邮件（简单可靠）
     */
    public void sendVerificationCode(String toEmail, String code) {
        SimpleMailMessage message = new SimpleMailMessage();

        message.setFrom(fromEmail);  //  不再写死
        message.setTo(toEmail);
        message.setSubject("aihusky网站邮箱验证码");

        message.setText(
                "您的注册验证码是：" + code +
                        "\n\n验证码有效期30分钟，请尽快完成注册。" +
                        "\n如果不是您本人操作，请忽略此邮件。"
        );

        mailSender.send(message);
    }
}
