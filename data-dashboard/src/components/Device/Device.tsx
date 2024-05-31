import React from "react";
import { Avatar, Grid, ListItemAvatar } from "@mui/material";
import {
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
} from "@mui/material";
import SmartphoneIcon from "@mui/icons-material/Smartphone";
import AddIcon from "@mui/icons-material/Add";
import SettingsIcon from "@mui/icons-material/Settings";

const Device = () => {
  const deviceNameList = ["Test Device"];
  const deviceImageList = [""];

  const handleDeviceSettingClick = () => {};
  const handleAddDeviceClick = () => {};

  return (
    <>
      <Typography sx={{ mt: 4, mb: 2 }} variant="h6" component="div">
        Devices
      </Typography>
      <List>
        <ListItem>
          <ListItemAvatar>
            <Avatar>
              <SmartphoneIcon></SmartphoneIcon>
            </Avatar>
          </ListItemAvatar>
          <ListItemText
            primary="Test Device"
            secondary="MAC: DE-AD-BE-EF-DE-AD"
          />
          <IconButton onClick={handleDeviceSettingClick}>
            <Avatar>
              <SettingsIcon></SettingsIcon>
            </Avatar>
          </IconButton>
        </ListItem>
        <ListItem>
          <IconButton onClick={handleAddDeviceClick}>
            <Avatar>
              <AddIcon></AddIcon>
            </Avatar>
          </IconButton>
          <ListItemText primary="Add a device" />
        </ListItem>
      </List>
    </>
  );
};

export default Device;
