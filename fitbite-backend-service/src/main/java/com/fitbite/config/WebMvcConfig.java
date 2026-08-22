package com.fitbite.config;

import com.fitbite.interceptor.JwtInterceptor;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web MVC 配置：注册 JWT 鉴权拦截器。
 *
 * 策略：拦截所有 /api/v1/**，但白名单放行注册、登录、已有公开业务接口与文档。
 * 当前仅 /api/v1/user/me 为受 Token 保护的示例接口；
 * 后续若要收紧某接口鉴权，只需将其从 excludePathPatterns 中移除即可。
 */
@Configuration
@RequiredArgsConstructor
public class WebMvcConfig implements WebMvcConfigurer {

    private final JwtInterceptor jwtInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(jwtInterceptor)
                .addPathPatterns("/api/v1/**")
                .excludePathPatterns(
                        // 认证相关公开接口
                        "/api/v1/user/register",
                        "/api/v1/user/login",
                        // 已有公开业务接口（保持现有前端功能可用）
                        "/api/v1/user/info/**",
                        "/api/v1/dish/**",
                        "/api/v1/diet/record/**",
                        "/api/v1/ai/**",
                        // Knife4j / OpenAPI 文档
                        "/doc.html",
                        "/v3/api-docs/**",
                        "/swagger-ui/**",
                        "/webjars/**"
                );
    }
}
