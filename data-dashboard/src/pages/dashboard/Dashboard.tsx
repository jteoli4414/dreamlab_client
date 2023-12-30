import { Box, Grid, Paper } from "@mui/material";
import React from "react";
import scss from "./Dashboard.module.scss";
import DataRibbon from "@/components/Dashboard/DataRibbon";
import TransactionsPerDay from "@/components/Dashboard/TransactionsPerDay/TransactionsPerDay";
import TransactionBottomRow from "@/components/Dashboard/TransactionBottomRow";

const Dashboard = () => {
  return (
    <Box>
      <Grid container gap={4} marginTop={2}>
        <DataRibbon></DataRibbon>
        <TransactionsPerDay></TransactionsPerDay>
      </Grid>
      <TransactionBottomRow></TransactionBottomRow>
    </Box>
  );
};

export default Dashboard;
