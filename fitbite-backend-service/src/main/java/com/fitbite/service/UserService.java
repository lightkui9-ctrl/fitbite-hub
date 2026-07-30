package com.fitbite.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.fitbite.domain.dto.UserSaveDTO;
import com.fitbite.domain.entity.SysUser;

public interface UserService extends IService<SysUser> {
    SysUser saveOrUpdateUser(UserSaveDTO dto);
    SysUser getByUsername(String username);
}