package com.fitbite.domain.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "用户登录请求参数")
public class UserLoginDTO {

    @Schema(description = "登录用户名", example = "XiaoLiang")
    private String username;

    @Schema(description = "登录密码", example = "123456")
    private String password;
}
