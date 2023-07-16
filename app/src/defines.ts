
export interface ApplyResponse {
    ok: boolean
    error?: string,
    message?: string,
    data?: object
}

export type Item = Record<string | 'type', any>

export interface ConditionResponse {
    ok: boolean
    message?: string,
}

export interface ApplyableInstance {
    apply(func_name: string): ApplyResponse
    canApply(func_name: string): ConditionResponse
    reset(): void
}


export interface LevelInfo {
    collection?: string
    level_id?:string
    diffculty?: string
    extra?: Record<string, any>
}

export interface LevelAchievement {
    score?: number,
    rating?: number,
    features?: Record<string, boolean>
}

export interface PlayableResult {
    succeed: boolean,
    archievement?: LevelAchievement,
    level?: LevelInfo
    items?: Item[]
}