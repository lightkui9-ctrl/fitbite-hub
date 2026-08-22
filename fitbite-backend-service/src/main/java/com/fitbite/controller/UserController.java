package com.fitbite.controller;

import com.fitbite.domain.dto.UserLoginDTO;
import com.fitbite.domain.dto.UserRegisterDTO;
import com.fitbite.domain.dto.UserSaveDTO;
import com.fitbite.domain.entity.SysUser;
import com.fitbite.domain.vo.LoginVO;
import com.fitbite.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "用户档案与认证接口")
@RestController
@RequestMapping("/api/v1/user")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:5173")
public class UserController {

    private final UserService userService;

    @Operation(summary = "用户注册（仅需用户名与密码，用户名唯一，密码 BCrypt 加密存储）")
    @PostMapping("/register")
    public SysUser register(@RequestBody UserRegisterDTO dto) {
        return userService.register(dto);
    }

    @Operation(summary = "用户登录（校验密码并签发 JWT）")
    @PostMapping("/login")
    public LoginVO login(@RequestBody UserLoginDTO dto) {
        return userService.login(dto);
    }

    @Operation(summary = "获取当前登录用户信息（需携带有效 Token 的受保护接口示例）")
    @GetMapping("/me")
    public SysUser me(HttpServletRequest request) {
        String username = (String) request.getAttribute("username");
        SysUser user = userService.getByUsername(username);
        if (user != null) {
            user.setPassword(null); // 脱敏
        }
        return user;
    }

    @Operation(summary = "保存或修改用户身体档案")
    @PostMapping("/save")
    public SysUser saveUser(@RequestBody UserSaveDTO dto) {
        return userService.saveOrUpdateUser(dto);
    }

    @Operation(summary = "根据用户名获取用户档案")
    @GetMapping("/info/{username}")
    public SysUser getUserInfo(@PathVariable String username) {
        SysUser user = userService.getByUsername(username);
        if (user != null) {
            user.setPassword(null); // 脱敏，避免泄露密码哈希
        }
        return user;
    }
}
