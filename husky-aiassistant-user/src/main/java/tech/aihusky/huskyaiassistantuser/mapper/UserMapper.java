package tech.aihusky.huskyaiassistantuser.mapper;


import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import tech.aihusky.huskyaiassistantuser.entry.User;

@Mapper
public interface UserMapper {

    @Select("SELECT * FROM user_account WHERE email = #{email}")
    User findByEmail(String email);

    @Insert("INSERT INTO user_account (email, password) VALUES (#{email}, #{password})")
    int insert(User user);

    // UserMapper.java
    @Update("""
    UPDATE user_account
    SET last_login_time = #{lastLoginTime},
        last_login_ip = #{lastLoginIp},
        area = #{area},
        device = #{device}
    WHERE user_id = #{userId}""")
    void updateLoginInfo(User user);
}
