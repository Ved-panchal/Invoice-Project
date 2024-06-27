import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    email: null,
    password: null,
    token: null,
    error: null,
};

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        loginSuccess(state, action) {
            state.isAuthenticated = true;
            state.user = action.payload.user;
            state.error = null;
        },
        loginFailure(state, action) {
            state.isAuthenticated = false;
            state.user = null;
            state.error = action.payload.error;
        },
        logout(state) {
            state.isAuthenticated = false;
            state.user = null;
            state.error = null;
        },
    },
});

// export const { loginSuccess, loginFailure, logout } = authSlice.actions;
export default authSlice.reducer;
