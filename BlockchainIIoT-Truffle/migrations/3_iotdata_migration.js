const IoTData = artifacts.require("IoTDataContract.sol");
        module.exports = function (deployer) {
          deployer.deploy(IoTData);
        };
        