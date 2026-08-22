package com.fitbite.controller;

import com.fitbite.domain.entity.Dish;
import com.fitbite.domain.entity.Ingredient;
import com.fitbite.mapper.DishMapper;
import com.fitbite.mapper.IngredientMapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "菜品与食材检索接口")
@RestController
@RequestMapping("/api/v1/dish")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:5173")
public class DishController {

    private final IngredientMapper ingredientMapper;
    private final DishMapper dishMapper;

    @Operation(summary = "获取所有可选食材列表")
    @GetMapping("/ingredients")
    public List<Ingredient> getAllIngredients() {
        return ingredientMapper.selectList(null);
    }

    @Operation(summary = "根据所选食材ID列表检索匹配菜品（ID为空则返回全部，并填充每道菜的食材标签）")
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