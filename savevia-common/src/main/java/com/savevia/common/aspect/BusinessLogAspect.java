package com.savevia.common.aspect;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.aspectj.lang.reflect.MethodSignature;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.lang.reflect.Method;
import java.lang.reflect.Parameter;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Aspect
@Component
@Slf4j
@RequiredArgsConstructor
public class BusinessLogAspect {

    private final ObjectMapper objectMapper;

    private static final String TRACE_ID = "traceId";

    @Pointcut("execution(* com.savevia.*.controller..*(..))")
    public void controllerPointcut() {}

    @Around("controllerPointcut()")
    public Object logControllerMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        // 生成 traceId
        String traceId = generateTraceId();
        MDC.put(TRACE_ID, traceId);

        long startTime = System.currentTimeMillis();
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Method method = signature.getMethod();

        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = method.getName();
        String fullMethodName = className + "." + methodName;

        // 获取请求信息
        HttpServletRequest request = getRequest();
        String requestUri = request != null ? request.getRequestURI() : "N/A";
        String httpMethod = request != null ? request.getMethod() : "N/A";
        String clientIp = request != null ? getClientIp(request) : "N/A";

        // 提取关键参数
        Map<String, Object> keyParams = extractKeyParameters(joinPoint, method);

        // [REQUEST] 记录请求
        log.info("[REQUEST] {} {} - {} - params: {}, ip: {}",
                httpMethod, requestUri, fullMethodName, formatParams(keyParams), clientIp);

        Object result = null;
        boolean success = false;
        String errorMessage = null;

        try {
            result = joinPoint.proceed();
            success = true;
            return result;
        } catch (Exception e) {
            errorMessage = e.getClass().getSimpleName() + ": " + e.getMessage();
            throw e;
        } finally {
            long duration = System.currentTimeMillis() - startTime;

            // [RESPONSE] 记录响应
            if (success) {
                String resultSummary = extractResultSummary(result);
                log.info("[RESPONSE] {} - success: true, duration: {}ms, result: {}",
                        fullMethodName, duration, resultSummary);
            } else {
                log.error("[RESPONSE] {} - success: false, duration: {}ms, error: {}",
                        fullMethodName, duration, errorMessage);
            }

            MDC.remove(TRACE_ID);
        }
    }

    private String generateTraceId() {
        HttpServletRequest request = getRequest();
        if (request != null) {
            String existingTraceId = request.getHeader("X-Trace-Id");
            if (existingTraceId != null && !existingTraceId.isEmpty()) {
                return existingTraceId;
            }
        }
        return UUID.randomUUID().toString().replace("-", "").substring(0, 16);
    }

    private HttpServletRequest getRequest() {
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        return attributes != null ? attributes.getRequest() : null;
    }

    private String getClientIp(HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("X-Real-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }
        // 取第一个IP（多级代理情况）
        if (ip != null && ip.contains(",")) {
            ip = ip.split(",")[0].trim();
        }
        return ip;
    }

    private Map<String, Object> extractKeyParameters(ProceedingJoinPoint joinPoint, Method method) {
        Map<String, Object> keyParams = new HashMap<>();
        Object[] args = joinPoint.getArgs();
        Parameter[] parameters = method.getParameters();

        for (int i = 0; i < parameters.length && i < args.length; i++) {
            Object arg = args[i];
            if (arg == null) continue;

            String paramName = parameters[i].getName();

            // 跳过 Spring 内部参数
            if (isSpringInternalParameter(arg)) continue;

            // 基本类型直接记录
            if (isPrimitiveOrWrapper(arg.getClass()) || arg instanceof String) {
                keyParams.put(paramName, arg);
            } else {
                // 复杂对象提取关键字段
                Map<String, Object> extracted = extractKeyFields(arg);
                if (!extracted.isEmpty()) {
                    keyParams.put(paramName, extracted);
                } else {
                    keyParams.put(paramName, arg.getClass().getSimpleName());
                }
            }
        }
        return keyParams;
    }

    private boolean isSpringInternalParameter(Object arg) {
        String className = arg.getClass().getName();
        return className.startsWith("org.springframework")
                || className.startsWith("jakarta.servlet");
    }

    private boolean isPrimitiveOrWrapper(Class<?> clazz) {
        return clazz.isPrimitive()
                || clazz == Boolean.class
                || clazz == Byte.class
                || clazz == Character.class
                || clazz == Short.class
                || clazz == Integer.class
                || clazz == Long.class
                || clazz == Float.class
                || clazz == Double.class;
    }

    private Map<String, Object> extractKeyFields(Object obj) {
        Map<String, Object> keyFields = new HashMap<>();
        try {
            Class<?> clazz = obj.getClass();
            for (java.lang.reflect.Field field : clazz.getDeclaredFields()) {
                String fieldName = field.getName().toLowerCase();
                // 只提取关键字段
                if (fieldName.contains("id") || fieldName.contains("email")
                        || fieldName.contains("name") || fieldName.contains("category")) {
                    field.setAccessible(true);
                    Object value = field.get(obj);
                    if (value != null) {
                        keyFields.put(field.getName(), value);
                    }
                }
            }
        } catch (Exception e) {
            // 忽略反射错误
        }
        return keyFields;
    }

    private String formatParams(Map<String, Object> params) {
        if (params.isEmpty()) {
            return "{}";
        }
        try {
            return objectMapper.writeValueAsString(params);
        } catch (Exception e) {
            return params.toString();
        }
    }

    private String extractResultSummary(Object result) {
        if (result == null) {
            return "null";
        }
        try {
            String json = objectMapper.writeValueAsString(result);
            // 截断过长的结果
            if (json.length() > 500) {
                return json.substring(0, 500) + "...(truncated)";
            }
            return json;
        } catch (Exception e) {
            return result.getClass().getSimpleName();
        }
    }
}
