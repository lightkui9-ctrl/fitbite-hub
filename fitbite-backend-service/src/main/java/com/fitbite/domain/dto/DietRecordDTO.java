package com.fitbite.domain.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import java.time.LocalDate;

@Data
@Schema(description = "饮食打卡请求参数")
public class DietRecordDTO {

    @Schema(description = "用户ID", example = "1")
    private Long userId;

    @Schema(description = "打卡日期", example = "2026-06-01")
    private LocalDate recordDate;

    @Schema(description = "餐次 (breakfast/lunch/dinner/snack)", example = "lunch")
    private String mealType;

    @Schema(description = "食物名称", example = "香煎鸡胸肉配西兰花")
    private String foodName;

    @Schema(description = "摄入热量 (kcal)", example = "450.0")
    private Double calories;

    @Schema(description = "蛋白质 (g)", example = "35.0")
    private Double protein;

    @Schema(description = "碳水 (g)", example = "40.0")
    private Double carbs;

    @Schema(description = "脂肪 (g)", example = "10.0")
    private Double fat;

    @Schema(description = "AI点评", example = "蛋白质搭配非常合理！")
    private String aiAdvice;
}