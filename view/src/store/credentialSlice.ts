import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "./rootReducer";

type Credential = {
    username?: string;
    password?: string;
};

const initialState: Credential = {
    username: "",
    password: "",
};

if (typeof window !== "undefined") {
    const state = localStorage.getItem("credential");
    if (state) {
        const parsedState = JSON.parse(state);
        initialState.username = parsedState.username;
        initialState.password = parsedState.password;
    }
}

const credentialSlice = createSlice({
    name: "credential",
    initialState,
    reducers: {
        setCredential: (state, action: PayloadAction<Credential>) => {
            state.username = action.payload.username;
            state.password = action.payload.password;
        },
        clearCredential: (state) => {
            state.username = "";
            state.password = "";
        },
    },
});

export const { setCredential, clearCredential } = credentialSlice.actions;

export const selectCredential = (state: RootState) => state.credential;

export default credentialSlice.reducer;
