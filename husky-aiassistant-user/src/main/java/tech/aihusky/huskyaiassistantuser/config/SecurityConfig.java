package tech.aihusky.huskyaiassistantuser.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf().disable() // 禁用 CSRF，否则 POST /login 可能被拦截
                .authorizeRequests()
                .antMatchers("/api/login", "/api/register").permitAll() // 登录注册接口放行
                .anyRequest().authenticated() // 其他接口需要认证
                .and()
                .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS); // JWT 无状态
        return http.build();
    }
}
