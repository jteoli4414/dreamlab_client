import { Grid } from "@mui/material";
import React from "react";
import DataCard from "@/components/Dashboard/DataCard";
import scss from "./DataRibbon.module.scss";

const DataRibbon = () => {
  return (
    <Grid container gap={2} className={scss.dataRibbon}>
      <Grid>
        <DataCard
          title={"Total Sales"}
          value={"462"}
          description={
            "The totals of all DataSoft products in the current financial year"
          }
        ></DataCard>
      </Grid>
      <Grid>
        <DataCard
          title={"Total Value"}
          value={"25,732.53"}
          description={"The total sales of the current financial year"}
        ></DataCard>
      </Grid>
      <Grid>
        <DataCard
          title={"Avg. Order Value"}
          value={"159.38"}
          description={
            "The average order value of all sales this current financial year"
          }
        ></DataCard>
      </Grid>
      <Grid>
        <DataCard
          title={"Conversion Rate"}
          value={"0.61%"}
          description={"How many pitches become sales"}
        ></DataCard>
      </Grid>
    </Grid>
  );
};

export default DataRibbon;
