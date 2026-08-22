package com.fitbite.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.fitbite.domain.dto.UserLoginDTO;
import com.fitbite.domain.dto.UserRegisterDTO;
import com.fitbite.domain.dto.UserSaveDTO;
import com.fitbite.domain.entity.SysUser;
import com.fitbite.domain.vo.LoginVO;

public interface UserService extends IService<SysUser> {
    SysUser saveOrUpdateUser(UserSaveDTO dto);
    SysUser getByUsername(String username);

    /** 用户注册：校验用户名唯一后，BCrypt 加密密码落库 */
    SysUser register(UserRegisterDTO dto);

    /** 用户登录：校验密码后签发 JWT，返回 Token 与脱敏用户信息 */
    LoginVO login(UserLoginDTO dto);
}