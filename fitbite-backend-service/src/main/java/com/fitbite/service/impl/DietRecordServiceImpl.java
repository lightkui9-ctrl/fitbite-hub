package com.fitbite.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fitbite.domain.dto.DietRecordDTO;
import com.fitbite.domain.entity.DietRecord;
import com.fitbite.domain.vo.DailyCalorieSummaryVO;
import com.fitbite.mapper.DietRecordMapper;
import com.fitbite.service.DietRecordService;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
public class DietRecordServiceImpl extends ServiceImpl<DietRecordMapper, DietRecord> implements DietRecordService {

    @Override
    public DietRecord addRecord(DietRecordDTO dto) {
        DietRecord record = new DietRecord();
        BeanUtils.copyProperties(dto, record);
        if (record.getRecordDate() == null) {
            record.setRecordDate(LocalDate.now());
        }
        this.save(record);
        return record;
    }

    @Override
    public DailyCalorieSummaryVO getDailySummary(Long userId, LocalDate date) {
        if (date == null) {
            date = LocalDate.now();
        }
        List<DietRecord> list = this.list(new LambdaQueryWrapper<DietRecord>()
                .eq(DietRecord::getUserId, userId)
                .eq(DietRecord::getRecordDate, date));

        double totalCalories = list.stream().mapToDouble(r -> r.getCalories() == null ? 0 : r.getCalories()).sum();
        double totalProtein = list.stream().mapToDouble(r -> r.getProtein() == null ? 0 : r.getProtein()).sum();
        double totalCarbs = list.stream().mapToDouble(r -> r.getCarbs() == null ? 0 : r.getCarbs()).sum();
        double totalFat = list.stream().mapToDouble(r -> r.getFat() == null ? 0 : r.getFat()).sum();

        DailyCalorieSummaryVO summary = new DailyCalorieSummaryVO();
        summary.setRecordDate(date);
        summary.setTotalCalories(totalCalories);
        summary.setTotalProtein(totalProtein);
        summary.setTotalCarbs(totalCarbs);
        summary.setTotalFat(totalFat);
        summary.setRecords(list);
        return summary;
    }
}