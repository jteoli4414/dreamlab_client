import React from "react";
import Paper from "@mui/material/Paper";
import Tooltip from "@mui/material/Tooltip";
import InfoOutlineIcon from "@mui/icons-material/InfoOutlined";
import { Grid, IconButton, Typography } from "@mui/material";
import scss from "./DataCard.module.scss";

export type DataCardProps = {
  title: string;
  value: string;
  description: string;
};

const DataCard = (props: DataCardProps) => {
  const { title, value, description } = props;
  return (
    <Paper className={scss.dataCard}>
      <div className={scss.header}>
        <Typography fontSize={"h6"} color={"lightslategrey"}>
          {title}
        </Typography>
        <Tooltip
          title={<Typography>{`${description} which is ${value}`}</Typography>}
        >
          <IconButton>
            <InfoOutlineIcon></InfoOutlineIcon>
          </IconButton>
        </Tooltip>
      </div>
      <Typography fontSize={"h4"}>{value}</Typography>
    </Paper>
  );
};

export default DataCard;
