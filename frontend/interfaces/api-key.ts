export interface IApiKey {
    id: string;
    name: string;
    key: string;
    created_at: string;
    last_used?: string;
    is_active: boolean;
}

export interface ICreateApiKey {
    name: string;
}
