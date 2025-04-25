#!/bin/bash

set -e

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BOLD}${BLUE}=======================================${NC}"
echo -e "${BOLD}${BLUE} Elastro Version Bump & Publish Tool ${NC}"
echo -e "${BOLD}${BLUE}=======================================${NC}"

# Check for bump2version
if ! command -v bump2version &> /dev/null; then
    echo -e "${RED}Error: bump2version is not installed.${NC}"
    echo -e "Installing bump2version..."
    pip install bump2version
fi

# Check for build
if ! python -c "import build" &> /dev/null; then
    echo -e "${RED}Error: build package is not installed.${NC}"
    echo -e "Installing build..."
    pip install build
fi

# Check for twine
if ! command -v twine &> /dev/null; then
    echo -e "${RED}Error: twine is not installed.${NC}"
    echo -e "Installing twine..."
    pip install twine
fi

# Get current version
CURRENT_VERSION=$(sed -n 's/current_version = \(.*\)/\1/p' .bumpversion.cfg)

echo -e "\n${BOLD}Current version:${NC} ${GREEN}$CURRENT_VERSION${NC}"

# Prompt for version bump type
echo -e "\n${BOLD}${YELLOW}STEP 1: Version Bump${NC}"
echo -e "This step will increase the version number in:"
echo -e "  - .bumpversion.cfg"
echo -e "  - pyproject.toml"
echo -e "  - elastro/__init__.py"
echo -e "\nPlease select how you want to bump the version:"
echo -e "  ${BOLD}1)${NC} patch (0.1.2 -> 0.1.3) - for bug fixes"
echo -e "  ${BOLD}2)${NC} minor (0.1.2 -> 0.2.0) - for new features"
echo -e "  ${BOLD}3)${NC} major (0.1.2 -> 1.0.0) - for backwards-incompatible changes"
echo -e "  ${BOLD}4)${NC} custom version"
echo -e "  ${BOLD}5)${NC} skip version bump"
read -p "Select an option (1-5): " BUMP_OPTION

if [[ $BUMP_OPTION == "1" ]]; then
    BUMP_TYPE="patch"
    echo -e "\nAbout to bump ${BOLD}patch${NC} version..."
    read -p "Proceed? (y/n): " CONFIRM
    if [[ $CONFIRM == "y" || $CONFIRM == "Y" ]]; then
        bump2version patch
        NEW_VERSION=$(sed -n 's/current_version = \(.*\)/\1/p' .bumpversion.cfg)
        echo -e "${GREEN}Version bumped to $NEW_VERSION${NC}"
    else
        echo -e "${YELLOW}Version bump skipped${NC}"
        NEW_VERSION=$CURRENT_VERSION
    fi
elif [[ $BUMP_OPTION == "2" ]]; then
    BUMP_TYPE="minor"
    echo -e "\nAbout to bump ${BOLD}minor${NC} version..."
    read -p "Proceed? (y/n): " CONFIRM
    if [[ $CONFIRM == "y" || $CONFIRM == "Y" ]]; then
        bump2version minor
        NEW_VERSION=$(sed -n 's/current_version = \(.*\)/\1/p' .bumpversion.cfg)
        echo -e "${GREEN}Version bumped to $NEW_VERSION${NC}"
    else
        echo -e "${YELLOW}Version bump skipped${NC}"
        NEW_VERSION=$CURRENT_VERSION
    fi
elif [[ $BUMP_OPTION == "3" ]]; then
    BUMP_TYPE="major"
    echo -e "\nAbout to bump ${BOLD}major${NC} version..."
    read -p "Proceed? (y/n): " CONFIRM
    if [[ $CONFIRM == "y" || $CONFIRM == "Y" ]]; then
        bump2version major
        NEW_VERSION=$(sed -n 's/current_version = \(.*\)/\1/p' .bumpversion.cfg)
        echo -e "${GREEN}Version bumped to $NEW_VERSION${NC}"
    else
        echo -e "${YELLOW}Version bump skipped${NC}"
        NEW_VERSION=$CURRENT_VERSION
    fi
elif [[ $BUMP_OPTION == "4" ]]; then
    read -p "Enter custom version (e.g., 0.2.1): " CUSTOM_VERSION
    echo -e "\nAbout to set version to ${BOLD}$CUSTOM_VERSION${NC}..."
    read -p "Proceed? (y/n): " CONFIRM
    if [[ $CONFIRM == "y" || $CONFIRM == "Y" ]]; then
        bump2version --new-version $CUSTOM_VERSION patch
        NEW_VERSION=$(sed -n 's/current_version = \(.*\)/\1/p' .bumpversion.cfg)
        echo -e "${GREEN}Version set to $NEW_VERSION${NC}"
    else
        echo -e "${YELLOW}Version change skipped${NC}"
        NEW_VERSION=$CURRENT_VERSION
    fi
elif [[ $BUMP_OPTION == "5" ]]; then
    echo -e "${YELLOW}Version bump skipped${NC}"
    NEW_VERSION=$CURRENT_VERSION
else
    echo -e "${RED}Invalid option. Exiting.${NC}"
    exit 1
fi

# Run tests
echo -e "\n${BOLD}${YELLOW}STEP 2: Run Tests${NC}"
echo -e "This step will run the test suite to ensure everything works."
read -p "Run tests before building? (y/n): " RUN_TESTS
if [[ $RUN_TESTS == "y" || $RUN_TESTS == "Y" ]]; then
    echo -e "\nRunning tests..."
    ./run_tests.sh --unit
    TEST_EXIT_CODE=$?
    if [ $TEST_EXIT_CODE -ne 0 ]; then
        echo -e "${RED}Tests failed. Fix the issues before building the package.${NC}"
        exit 1
    else
        echo -e "${GREEN}All tests passed!${NC}"
    fi
else
    echo -e "${YELLOW}Tests skipped. Make sure your code is properly tested!${NC}"
fi

# Build package
echo -e "\n${BOLD}${YELLOW}STEP 3: Build Package${NC}"
echo -e "This step will build the distribution packages (wheel and sdist)."
read -p "Build the package? (y/n): " BUILD_PACKAGE
if [[ $BUILD_PACKAGE == "y" || $BUILD_PACKAGE == "Y" ]]; then
    echo -e "\nBuilding package..."
    python -m build
    echo -e "${GREEN}Package built successfully!${NC}"
else
    echo -e "${YELLOW}Build skipped${NC}"
    exit 0
fi

# Upload to PyPI
echo -e "\n${BOLD}${YELLOW}STEP 4: Upload to PyPI${NC}"
echo -e "This step will upload the package to PyPI."
echo -e "${RED}WARNING: This action cannot be undone!${NC}"
read -p "Upload to PyPI? (y/n): " UPLOAD_PACKAGE
if [[ $UPLOAD_PACKAGE == "y" || $UPLOAD_PACKAGE == "Y" ]]; then
    echo -e "\nAbout to upload ${BOLD}elastro-$NEW_VERSION${NC} to PyPI..."
    read -p "Proceed? (y/n): " CONFIRM_UPLOAD
    if [[ $CONFIRM_UPLOAD == "y" || $CONFIRM_UPLOAD == "Y" ]]; then
        echo -e "\nUploading to PyPI..."
        twine upload dist/elastro-$NEW_VERSION-py3-none-any.whl dist/elastro-$NEW_VERSION.tar.gz
        echo -e "${GREEN}Package uploaded to PyPI successfully!${NC}"
    else
        echo -e "${YELLOW}Upload skipped${NC}"
    fi
else
    echo -e "${YELLOW}Upload skipped${NC}"
fi

echo -e "\n${BOLD}${GREEN}Process completed!${NC}" 