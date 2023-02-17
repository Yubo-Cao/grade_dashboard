import { ReactElement } from "react";
import "./global.css";
import { Provider } from "react-redux";
import store from "@/store";
import Head from "next/head";
import Link from "next/link";

interface AppProps {
  Component: React.ElementType;
  pageProps: Record<string, unknown>;
}

export default function App({ Component, pageProps }: AppProps): ReactElement {
  return (
    <Provider store={store}>
      <Head>
        <Link rel="icon" href="/favicon.png" />
      </Head>
      <Component {...pageProps} />
    </Provider>
  );
}
