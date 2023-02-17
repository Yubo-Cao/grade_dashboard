import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "./rootReducer";

type Config = {
  weighted: boolean;
  normalize: boolean;
  notify: boolean;
  backendUrl?: string;
};

const initialState: Config = {
  weighted: false,
  normalize: false,
  notify: false,
};

if (typeof window !== "undefined") {
  const state = localStorage.getItem("config");
  if (state) {
    const parsedState = JSON.parse(state);
    initialState.weighted = parsedState.weighted;
    initialState.normalize = parsedState.normalize;
    initialState.notify = parsedState.notify;
    initialState.backendUrl = parsedState.backendUrl;
  }
}

const configSlice = createSlice({
  name: "config",
  initialState,
  reducers: {
    setConfig: (state, action: PayloadAction<Config>) => {
      state.weighted = action.payload.weighted;
      state.normalize = action.payload.normalize;
      state.notify = action.payload.notify;
      state.backendUrl = action.payload.backendUrl;
    },
  },
});

export const { setConfig } = configSlice.actions;

export const selectConfig = (state: RootState) => state.config;

export default configSlice.reducer;
