package com.fitbite.domain.vo;

import com.fitbite.domain.entity.SysUser;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "登录成功返回体（Token + 脱敏用户信息）")
public class LoginVO {

    @Schema(description = "JWT 令牌")
    private String token;

    @Schema(description = "用户信息（已脱敏，不含密码）")
    private SysUser user;
}
