package com.fitbite.controller;

import com.fitbite.domain.dto.UserSaveDTO;
import com.fitbite.domain.entity.SysUser;
import com.fitbite.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "用户档案管理接口")
@RestController
@RequestMapping("/api/v1/user")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class UserController {

    private final UserService userService;

    @Operation(summary = "保存或修改用户身体档案")
    @PostMapping("/save")
    public SysUser saveUser(@RequestBody UserSaveDTO dto) {
        return userService.saveOrUpdateUser(dto);
    }

    @Operation(summary = "根据用户名获取用户档案")
    @GetMapping("/info/{username}")
    public SysUser getUserInfo(@PathVariable String username) {
        return userService.getByUsername(username);
    }
}