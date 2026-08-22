package com.fitbite.interceptor;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fitbite.util.JwtUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.util.Map;

/**
 * JWT 鉴权拦截器：对受保护接口校验请求头中的 Bearer Token，
 * 无效或缺失则返回 401。校验通过后将用户名写入 request 属性供后续使用。
 *
 * 拦截规则在 WebMvcConfig 中配置（白名单放行注册/登录等公开接口）。
 */
@Component
@RequiredArgsConstructor
public class JwtInterceptor implements HandlerInterceptor {

    private final JwtUtil jwtUtil;

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 放行 CORS 预检请求（OPTIONS），否则浏览器发 POST 前的预检会被拦截器挡住返回 401，
        // 导致前端报"网络错误"
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            return true;
        }
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            writeUnauthorized(response, "缺失或非法的 Authorization 头");
            return false;
        }
        String token = authHeader.substring(7);
        if (!jwtUtil.validateToken(token)) {
            writeUnauthorized(response, "Token 无效或已过期");
            return false;
        }
        String username = jwtUtil.parseUsername(token);
        request.setAttribute("username", username);
        return true;
    }

    private void writeUnauthorized(HttpServletResponse response, String msg) throws Exception {
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding("UTF-8");
        Map<String, Object> body = Map.of("code", 401, "msg", msg);
        response.getWriter().write(OBJECT_MAPPER.writeValueAsString(body));
    }
}
