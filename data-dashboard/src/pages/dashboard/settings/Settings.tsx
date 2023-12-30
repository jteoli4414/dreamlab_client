import React from "react";
import {
  Box,
  FormControl,
  FormControlLabel,
  Grid,
  Switch,
  Typography,
  Button,
} from "@mui/material";

const Settings = () => {
  const [showRevenue, setShowRevenue] = React.useState(true);
  const [showProfit, setShowProfit] = React.useState(true);
  const [showOrders, setShowOrders] = React.useState(true);
  const [showCustomers, setShowCustomers] = React.useState(true);

  const handleShowRevenueChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setShowRevenue(event.target.checked);
  };
  const handleShowProfitChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setShowProfit(event.target.checked);
  };
  const handleShowOrdersChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setShowOrders(event.target.checked);
  };
  const handleShowCustomersChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setShowCustomers(event.target.checked);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event?.preventDefault();
  };
  return (
    <>
      <h1>Settings</h1>
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard Features
        </Typography>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12}></Grid>
            <FormControl component="fieldset">
              <FormControlLabel
                control={
                  <Switch
                    checked={showRevenue}
                    onChange={handleShowRevenueChange}
                  ></Switch>
                }
                label="Revenue"
              ></FormControlLabel>
              <FormControlLabel
                control={
                  <Switch
                    checked={showProfit}
                    onChange={handleShowProfitChange}
                  ></Switch>
                }
                label="Profit"
              ></FormControlLabel>
              <FormControlLabel
                control={
                  <Switch
                    checked={showOrders}
                    onChange={handleShowOrdersChange}
                  ></Switch>
                }
                label="Orders"
              ></FormControlLabel>
              <FormControlLabel
                control={
                  <Switch
                    checked={showCustomers}
                    onChange={handleShowCustomersChange}
                  ></Switch>
                }
                label="Customers"
              ></FormControlLabel>
            </FormControl>
            <Grid item xs={12}>
              <Button type="submit" variant="contained" color="primary">
                Save Settings
              </Button>
            </Grid>
          </Grid>
        </form>
      </Box>
    </>
  );
};

export default Settings;
