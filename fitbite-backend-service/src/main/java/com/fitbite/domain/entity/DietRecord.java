package com.fitbite.domain.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("diet_record")
public class DietRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private LocalDate recordDate;

    private String mealType;

    private String foodName;

    private Double calories;

    private Double protein;

    private Double carbs;

    private Double fat;

    private String aiAdvice;

    private LocalDateTime createdAt;

    @TableLogic
    private Integer deleted;
}