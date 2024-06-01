import React, { useState } from "react";
import {
  Typography,
  Box,
  Paper,
  Grid,
  Avatar,
  TextField,
  FormControlLabel,
  Checkbox,
  Button,
} from "@mui/material";
import { useSession } from "next-auth/react";

const Journal = () => {
  const { data: session } = useSession();
  const names = session?.user?.name ? session.user.name.split(" ") : [];
  const firstName = names[0];
  const lastName = names?.length > 1 ? names[names.length - 1] : "";
  const emailAddress = session?.user?.email;

  const handleFormChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked } = event.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: name === "recieveEmails" ? checked : value,
    }));
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    console.log(formData);
  };

  const [formData, setFormData] = useState({
    firstName: firstName,
    lastName: lastName,
    email: emailAddress,
    password: "",
    confirmPassword: "",
    recieveEmails: false,
  });

  return (
    <>
      <h1>{session ? session?.user?.name + "'s" : "My "} Dream Journal</h1>
      <Box>
        <Paper sx={{ padding: "1rem 2rem" }}>
          <Grid container justifyContent="center">
            <Grid item xs={12} sm={8} md={6}>
              <Box display="flex" flexDirection="column" alignItems="center">
                <Avatar
                  sx={{
                    height: 100,
                    width: 100,
                    marginBottom: 2,
                  }}
                  src={session?.user?.image as string}
                ></Avatar>
              </Box>
              <form
                onSubmit={handleSubmit}
                style={{ maxWidth: 600, margin: "0 auto" }}
              >
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      required
                      fullWidth
                      label="First Name"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleFormChange}
                    ></TextField>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      required
                      fullWidth
                      label="Last Name"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleFormChange}
                    ></TextField>
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      required
                      fullWidth
                      type="email"
                      label="Email"
                      name="email"
                      value={formData.email}
                      onChange={handleFormChange}
                    ></TextField>
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      required
                      fullWidth
                      type="password"
                      label="Password"
                      name="password"
                      value={formData.password}
                      onChange={handleFormChange}
                    ></TextField>
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      required
                      fullWidth
                      type="password"
                      label="Confirm Password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleFormChange}
                    ></TextField>
                  </Grid>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          name="recieveEmails"
                          checked={formData.recieveEmails}
                          onChange={handleFormChange}
                          color="primary"
                        ></Checkbox>
                      }
                      label="Receive sales analytics emails"
                    ></FormControlLabel>
                  </Grid>
                  <Grid item xs={12}>
                    <Button type="submit" variant="contained" color="primary">
                      Save Changes
                    </Button>
                  </Grid>
                </Grid>
              </form>
            </Grid>
          </Grid>
        </Paper>
      </Box>
    </>
  );
};

export default Journal;
