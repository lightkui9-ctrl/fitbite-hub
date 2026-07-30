package com.fitbite.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.fitbite.domain.dto.DietRecordDTO;
import com.fitbite.domain.entity.DietRecord;
import com.fitbite.domain.vo.DailyCalorieSummaryVO;

import java.time.LocalDate;

public interface DietRecordService extends IService<DietRecord> {
    DietRecord addRecord(DietRecordDTO dto);
    DailyCalorieSummaryVO getDailySummary(Long userId, LocalDate date);
}