package com.fitbite.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fitbite.domain.dto.UserLoginDTO;
import com.fitbite.domain.dto.UserRegisterDTO;
import com.fitbite.domain.dto.UserSaveDTO;
import com.fitbite.domain.entity.SysUser;
import com.fitbite.domain.vo.LoginVO;
import com.fitbite.mapper.SysUserMapper;
import com.fitbite.service.UserService;
import com.fitbite.util.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class UserServiceImpl extends ServiceImpl<SysUserMapper, SysUser> implements UserService {

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();
    private final JwtUtil jwtUtil;

    @Override
    public SysUser saveOrUpdateUser(UserSaveDTO dto) {
        SysUser existUser = getByUsername(dto.getUsername());
        if (existUser == null) {
            throw new RuntimeException("用户不存在: " + dto.getUsername());
        }
        // 只更新 DTO 中非 null 的字段，避免把用户已有档案被 null 覆盖
        LambdaUpdateWrapper<SysUser> wrapper = new LambdaUpdateWrapper<SysUser>()
                .eq(SysUser::getId, existUser.getId());
        if (dto.getGender() != null) wrapper.set(SysUser::getGender, dto.getGender());
        if (dto.getAge() != null) wrapper.set(SysUser::getAge, dto.getAge());
        if (dto.getHeight() != null) wrapper.set(SysUser::getHeight, dto.getHeight());
        if (dto.getWeight() != null) wrapper.set(SysUser::getWeight, dto.getWeight());
        if (dto.getTargetWeight() != null) wrapper.set(SysUser::getTargetWeight, dto.getTargetWeight());
        if (dto.getActivityLevel() != null) wrapper.set(SysUser::getActivityLevel, dto.getActivityLevel());
        wrapper.set(SysUser::getUpdatedAt, LocalDateTime.now());
        this.update(wrapper);
        // 返回最新数据（脱敏）
        SysUser updated = getById(existUser.getId());
        updated.setPassword(null);
        return updated;
    }

    @Override
    public SysUser getByUsername(String username) {
        return this.getOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username));
    }

    @Override
    public SysUser register(UserRegisterDTO dto) {
        if (!dto.getPassword().equals(dto.getConfirmPassword())) {
            throw new RuntimeException("两次输入的密码不一致");
        }
        if (getByUsername(dto.getUsername()) != null) {
            throw new RuntimeException("用户名已存在: " + dto.getUsername());
        }
        // 注册只建账号，个人档案（性别/年龄/身高/体重/目标体重/活动量）由用户登录后自行完善
        SysUser user = new SysUser();
        user.setUsername(dto.getUsername());
        user.setPassword(passwordEncoder.encode(dto.getPassword()));
        // 显式置 null：即便 register 路径只 set 上面两字段，也明确列出 intent，避免后续维护误把档案拷过来
        user.setGender(null);
        user.setAge(null);
        user.setHeight(null);
        user.setWeight(null);
        user.setTargetWeight(null);
        user.setActivityLevel(null);
        LocalDateTime now = LocalDateTime.now();
        user.setCreatedAt(now);
        user.setUpdatedAt(now);
        this.save(user);
        user.setPassword(null); // 脱敏，不向下游返回密码
        return user;
    }

    @Override
    public LoginVO login(UserLoginDTO dto) {
        SysUser user = getByUsername(dto.getUsername());
        if (user == null || user.getPassword() == null
                || !passwordEncoder.matches(dto.getPassword(), user.getPassword())) {
            throw new RuntimeException("用户名或密码错误");
        }
        String token = jwtUtil.generateToken(user.getUsername());
        LoginVO vo = new LoginVO();
        user.setPassword(null);
        vo.setToken(token);
        vo.setUser(user);
        return vo;
    }
}