package com.fitbite.domain.vo;

import com.fitbite.domain.entity.DietRecord;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import java.time.LocalDate;
import java.util.List;

@Data
@Schema(description = "每日热量账本汇总视图")
public class DailyCalorieSummaryVO {

    @Schema(description = "打卡日期")
    private LocalDate recordDate;

    @Schema(description = "当日总摄入热量 (kcal)")
    private Double totalCalories;

    @Schema(description = "当日总蛋白质 (g)")
    private Double totalProtein;

    @Schema(description = "当日总碳水 (g)")
    private Double totalCarbs;

    @Schema(description = "当日总脂肪 (g)")
    private Double totalFat;

    @Schema(description = "当日明细记录")
    private List<DietRecord> records;
}