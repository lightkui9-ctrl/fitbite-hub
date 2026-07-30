package com.fitbite.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.fitbite.domain.entity.DietRecord;

public interface DietRecordMapper extends BaseMapper<DietRecord> {
    // 继承 BaseMapper，已自动具备 CRUD 能力
}