use serde::{Deserialize, Serialize};
use validator::{Validate, ValidationError};
use std::collections::HashMap;

/// 用户创建请求模型 - 类似 Pydantic 的数据验证模型
#[derive(Debug, Serialize, Deserialize, Validate)]
pub struct CreateUserRequest {
    #[validate(length(min = 3, max = 50, message = "用户名长度必须在3-50个字符之间"))]
    pub username: String,
    
    #[validate(email(message = "邮箱格式不正确"))]
    pub email: String,
    
    #[validate(length(min = 8, message = "密码长度必须至少为8个字符"))]
    #[validate(custom = "validate_password_strength")]
    pub password: String,
    
    #[validate(length(max = 500, message = "个人简介不能超过500个字符"))]
    pub bio: Option<String>,
    
    #[validate]
    pub metadata: Option<UserMetadata>,
}

/// 用户元数据 - 嵌套验证
#[derive(Debug, Serialize, Deserialize, Validate)]
pub struct UserMetadata {
    #[validate(range(min = 0, max = 150, message = "年龄必须在0-150之间"))]
    pub age: Option<u8>,
    
    pub interests: Option<Vec<String>>,
    
    #[validate(custom = "validate_phone_number")]
    pub phone: Option<String>,
    
    #[serde(flatten)]
    pub extra: Option<HashMap<String, serde_json::Value>>,
}

/// 自定义密码强度验证函数
fn validate_password_strength(password: &str) -> Result<(), ValidationError> {
    // 检查密码是否包含至少一个数字
    if !password.chars().any(|c| c.is_ascii_digit()) {
        return Err(ValidationError::new("密码必须包含至少一个数字"));
    }
    
    // 检查密码是否包含至少一个特殊字符
    let special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?";
    if !password.chars().any(|c| special_chars.contains(c)) {
        return Err(ValidationError::new("密码必须包含至少一个特殊字符"));
    }
    
    Ok(())
}

/// 自定义电话号码验证函数
fn validate_phone_number(phone: &str) -> Result<(), ValidationError> {
    // 简单的电话号码验证示例
    if !phone.chars().all(|c| c.is_ascii_digit() || c == '+' || c == '-') {
        return Err(ValidationError::new("电话号码格式不正确"));
    }
    
    Ok(())
}

/// 用于演示如何使用验证功能的函数
pub fn validate_user_input(input: &str) -> Result<CreateUserRequest, String> {
    // 尝试解析 JSON 为 CreateUserRequest
    let user_request: CreateUserRequest = serde_json::from_str(input)
        .map_err(|e| format!("JSON 解析错误: {}", e))?;
    
    // 验证数据
    user_request.validate()
        .map_err(|e| format!("验证错误: {}", e))?;
    
    Ok(user_request)
}

/// 用于演示如何在 API 处理程序中使用验证
pub async fn create_user_handler(
    // 这里可以使用 axum 的 Json 提取器
    // Json(payload): Json<CreateUserRequest>,
    payload: CreateUserRequest,
) -> Result<String, String> {
    // 验证数据 (如果使用 axum 的 Json 提取器，可以添加自定义提取器来自动验证)
    payload.validate().map_err(|e| format!("验证错误: {}", e))?;
    
    // 处理验证通过的数据...
    Ok(format!("用户 {} 创建成功!", payload.username))
}
