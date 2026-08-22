package com.fitbite.domain.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "用户注册请求参数（仅需用户名与密码，个人档案后续在档案页补全）")
public class UserRegisterDTO {

    @Schema(description = "登录用户名", example = "XiaoLiang")
    private String username;

    @Schema(description = "登录密码（明文，后端 BCrypt 加密存储）", example = "123456")
    private String password;

    @Schema(description = "确认密码（需与 password 一致）", example = "123456")
    private String confirmPassword;
}
