package com.fitbite.controller;

import com.fitbite.domain.entity.Dish;
import com.fitbite.domain.entity.Ingredient;
import com.fitbite.mapper.DishMapper;
import com.fitbite.mapper.IngredientMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/dish")
@RequiredArgsConstructor
@CrossOrigin
public class DishController {

    private final IngredientMapper ingredientMapper;
    private final DishMapper dishMapper;

    // 1. 获取所有可选食材列表
    @GetMapping("/ingredients")
    public List<Ingredient> getAllIngredients() {
        return ingredientMapper.selectList(null);
    }

    // 2. 根据选中的食材ID列表查询匹配的菜品
    @PostMapping("/search")
    public List<Dish> searchDishes(@RequestBody List<Long> ingredientIds) {
        List<Dish> dishes;
        if (ingredientIds == null || ingredientIds.isEmpty()) {
            dishes = dishMapper.selectList(null);
        } else {
            dishes = dishMapper.selectDishesByIngredientIds(ingredientIds);
        }

        // 填充每个菜品的食材标签
        for (Dish dish : dishes) {
            dish.setIngredientNames(dishMapper.selectIngredientNamesByDishId(dish.getId()));
        }
        return dishes;
    }
}