package com.fitbite.controller;

import com.fitbite.domain.dto.DietRecordDTO;
import com.fitbite.domain.entity.DietRecord;
import com.fitbite.domain.vo.DailyCalorieSummaryVO;
import com.fitbite.service.DietRecordService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;

@Tag(name = "饮食打卡账本接口")
@RestController
@RequestMapping("/api/v1/diet/record")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class DietRecordController {

    private final DietRecordService dietRecordService;

    @Operation(summary = "添加一笔饮食打卡记录")
    @PostMapping("/add")
    public DietRecord addRecord(@RequestBody DietRecordDTO dto) {
        return dietRecordService.addRecord(dto);
    }

    @Operation(summary = "获取指定日期的热量账本汇总及明细")
    @GetMapping("/summary")
    public DailyCalorieSummaryVO getDailySummary(
            @RequestParam Long userId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        return dietRecordService.getDailySummary(userId, date);
    }
}