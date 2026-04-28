provider "azurerm" {
  features {}
}

provider "aws" {
  region = var.aws_region
}

resource "azurerm_resource_group" "foundation" {
  name     = "rg-${var.project_name}-foundation-${var.environment}"
  location = var.location
}

# --- Foundation Control Plane (AKS) ---

resource "azurerm_kubernetes_cluster" "zone_k8s" {
  name                = "aks-zone-iq-${var.environment}"
  location            = azurerm_resource_group.foundation.location
  resource_group_name = azurerm_resource_group.foundation.name
  dns_prefix          = "zone-k8s"

  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }
}

# --- Secure Hub Networking (Azure Hub VNet) ---

resource "azurerm_virtual_network" "hub" {
  name                = "vnet-hub-${var.environment}"
  location            = azurerm_resource_group.foundation.location
  resource_group_name = azurerm_resource_group.foundation.name
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "gateway" {
  name                 = "GatewaySubnet" # Mandatory name for VNet Gateway
  resource_group_name  = azurerm_resource_group.foundation.name
  virtual_network_name = azurerm_virtual_network.hub.name
  address_prefixes     = ["10.0.1.0/24"]
}

# --- Shared Key Management (KeyVault) ---

resource "azurerm_key_vault" "foundation_vault" {
  name                        = "kv-zone-foundation-${var.environment}"
  location                    = azurerm_resource_group.foundation.location
  resource_group_name         = azurerm_resource_group.foundation.name
  enabled_for_disk_encryption = true
  tenant_id                   = var.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"
}

# --- Multi-Cloud Global Transit (AWS Transit Gateway) ---

resource "aws_ec2_transit_gateway" "global_hub" {
  description = "Multi-cloud global data hub transit"
}
