package tech.aihusky.huskyaiassistantuser.mapper;


import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import tech.aihusky.huskyaiassistantuser.entry.User;

@Mapper
public interface UserMapper {

    @Select("SELECT * FROM user WHERE email = #{email}")
    User findByEmail(String email);

    @Insert("INSERT INTO user (email, password) VALUES (#{email}, #{password})")
    int insert(User user);
}
