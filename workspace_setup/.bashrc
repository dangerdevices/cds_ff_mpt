#! /usr/bin/env bash

export LM_LICENSE_FILE="5280@172.18.3.25"
export CDS_LIC_FILE="5280@172.18.3.25"

export ASSURAHOME="/data/cadence/installs/ASSURA41"
export SPECTREHOME="/data/cadence/installs/SPECTRE181"
export CDS_Netlisting_Mode="Analog"
export CDSHOME="/data/cadence/installs/IC617"
export CDS_AUTO_64BIT="ALL"

PATH="$PATH:$HOME/.local/bin:$SPECTREHOME/tools.lnx86/bin:$SPECTREHOME/tools.lnx86/dfII:$SPECTREHOME/tools.lnx86/dfII/bin:$CDSHOME/tools/dfII/bin:$CDSHOME/tools:$CDSHOME/tools/bin:$ASSURAHOME/tools/bin:$ASSURAHOME/tools/assura/bin:/data/bin"
export PATH

### Setup BAG
source .bashrc_bag
