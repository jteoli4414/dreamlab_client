import Head from "next/head";
import SideMenu from "../SideMenu";
import scss from "./Layout.module.scss";
import { useSession } from "next-auth/react";
import React from "react";
import Footer from "@/components/Footer";

const Layout = (props: any) => {
  const { data: session } = useSession();
  return (
    <>
      <Head>
        <title>My Sleep Lab</title>
        <meta name="description" content="My Sleep Lab" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main
        className={scss.layout}
        style={{ padding: session ? "0 24px 0 80px" : 0 }}
      >
        {session && <SideMenu />}
        {props.children}
        <Footer></Footer>
      </main>
    </>
  );
};

export default Layout;
