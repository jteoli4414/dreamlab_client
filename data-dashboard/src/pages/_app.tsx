import { SessionProvider } from "next-auth/react";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import React from "react";
import darkTheme from "@/theme/lighttheme";
import lightTheme from "@/theme/darktheme";
import Header from "@/components/Header";
import Layout from "@/components/Layout";

const ColorModeContext = React.createContext({ toggleColorMode: () => {} });

const App = ({ Component, pageProps: { session, ...pageProps } }) => {
  const [mode, setMode] = React.useState<"light" | "dark">("dark");
  const colorMode = React.useMemo(
    () => ({
      toggleColorMode: () => {
        setMode((prevMode) => (prevMode === "light" ? "dark" : "light"));
      },
    }),
    []
  );

  const darkThemeChosen = React.useMemo(
    () =>
      createTheme({
        ...darkTheme,
      }),
    [mode]
  );
  const lightThemeChosen = React.useMemo(
    () =>
      createTheme({
        ...lightTheme,
      }),
    [mode]
  );

  return (
    <ColorModeContext.Provider value={colorMode}>
      <ThemeProvider
        theme={mode === "dark" ? darkThemeChosen : lightThemeChosen}
      >
        <SessionProvider session={session}>
          <CssBaseline></CssBaseline>
          <Header ColorModeContext={ColorModeContext}></Header>
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </SessionProvider>
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
};

export default App;
