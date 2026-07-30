package com.fitbite.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fitbite.domain.dto.UserSaveDTO;
import com.fitbite.domain.entity.SysUser;
import com.fitbite.mapper.SysUserMapper;
import com.fitbite.service.UserService;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

@Service
public class UserServiceImpl extends ServiceImpl<SysUserMapper, SysUser> implements UserService {

    @Override
    public SysUser saveOrUpdateUser(UserSaveDTO dto) {
        SysUser existUser = getByUsername(dto.getUsername());
        if (existUser == null) {
            existUser = new SysUser();
        }
        BeanUtils.copyProperties(dto, existUser);
        this.saveOrUpdate(existUser);
        return existUser;
    }

    @Override
    public SysUser getByUsername(String username) {
        return this.getOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username));
    }
}