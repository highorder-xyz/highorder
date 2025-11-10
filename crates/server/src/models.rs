use sea_orm::entity::prelude::*;
use chrono::Utc;

// Define the User entity
#[derive(Clone, Debug, PartialEq, Eq, DeriveEntityModel)]
#[sea_orm(table_name = "users")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,
    pub username: String,
    pub email: String,
    #[sea_orm(column_type = "Text", nullable)]
    pub bio: Option<String>,
    pub created_at: DateTimeWithTimeZone,
    pub updated_at: DateTimeWithTimeZone,
}

// Define the relationships for the User entity
#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {}

// Implement ActiveModelBehavior for the User entity
impl ActiveModelBehavior for ActiveModel {
    // Called before insert
    fn before_save(mut self, insert: bool) -> Result<Self, DbErr> {
        let now = Utc::now().naive_utc().and_utc();
        
        if insert {
            self.created_at = Set(now);
        }
        self.updated_at = Set(now);
        
        Ok(self)
    }
}

// Define the CRUD operations for the User entity
impl Entity {
    pub fn find_by_id(id: i32) -> Select<Entity> {
        Self::find().filter(Column::Id.eq(id))
    }
    
    pub fn find_by_username(username: &str) -> Select<Entity> {
        Self::find().filter(Column::Username.eq(username))
    }
    
    pub fn find_by_email(email: &str) -> Select<Entity> {
        Self::find().filter(Column::Email.eq(email))
    }
}
